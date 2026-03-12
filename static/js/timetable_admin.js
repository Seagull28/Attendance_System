(function($) {
    $(document).ready(function() {
      var $department = $('#id_department');
      var $section = $('#id_section');
      var $subject = $('#id_subject');
  
      function updateSections() {
        var department = $department.val();
        if (department) {
          $.get('/admin/face_recognition_app/section/by-department/', {
            department: department
          })
          .done(function(data) {
            $section.empty();
            $section.append($('<option value="">---------</option>'));
            $.each(data.sections, function(index, item) {
              $section.append($('<option></option>')
                .attr('value', item.id)
                .text(item.name));
            });
            updateSubjects(); // auto-update subjects too
          })
          .fail(function(jqXHR, textStatus, errorThrown) {
            console.error('Failed to fetch sections:', textStatus, errorThrown);
          });
        } else {
          $section.empty().append($('<option value="">---------</option>'));
          $subject.empty();
        }
      }
  
      function updateSubjects() {
        var department = $department.val();
        var section = $section.val();
  
        if (department && section) {
          $.get('/admin/face_recognition_app/subject/by-department-section/', {
            department: department,
            section: section
          })
          .done(function(data) {
            $subject.empty();
            $.each(data.subjects, function(index, item) {
              $subject.append($('<option></option>')
                .attr('value', item.id)
                .text(item.name));
            });
          })
          .fail(function(jqXHR, textStatus, errorThrown) {
            console.error('Failed to fetch subjects:', textStatus, errorThrown);
          });
        } else {
          $subject.empty();
        }
      }
  
      $department.change(updateSections);
      $section.change(updateSubjects);
  
      // If department already selected (editing existing form), trigger updates
      if ($department.val()) {
        updateSections();
      }
    });
  })(window.jQuery);
  